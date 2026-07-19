# v3 sweep launch result

Track 1, `scripts/ford_sweep_driver.py --config v3`. First actual attempt, not a relaunch.

Config: depths [0.10, 0.15, 0.30, 0.45, 0.60], velocities [0.5, 1.0, 1.5, 2.0],
n_grid=128, 3 vehicle classes = 60 runs expected.

Job 833349, partition gh, node c611-132. State COMPLETED, ExitCode 0:0,
elapsed 00:07:12 (start 2026-07-15T05:46:29, end 2026-07-15T05:53:35).
Rows produced: 60/60 as expected.

## Headline

**The run completed cleanly and the results are not usable.** rc=0, 60/60 rows,
no stderr, every liveness signal green. The vehicle body is hollow at n_grid=128
and 0 of 60 rows pass the density plausibility check. This is a silent success:
the job's own exit status is not evidence the science is valid.

## Pre-registered prediction vs result

Prediction was written before the run landed. Provenance note kept from the original:
my earlier in-session statement was only that density would "move" when n_grid changed,
which is direction-agnostic and unfalsifiable. The directional call below was made fresh
at launch, with a mechanism.

Predicted: SUV density comes back ABOVE 308.13, all three classes rise.
Predicted mechanism: halving h sharpens the voxel silhouette, trimming boundary cells
that overhang the true body, so solid_volume shrinks modestly and density converges
upward.

Result:

| class  | mass_kg | vol64 m3 | vol128 m3 | dens64 | dens128 | factor | plausible |
|--------|---------|----------|-----------|--------|---------|--------|-----------|
| sedan  | 1390.0  | 4.7352   | 2.5522    | 293.55 | 544.63  | 1.86x  | False     |
| suv    | 1990.0  | 6.4583   | 3.4571    | 308.13 | 575.62  | 1.87x  | False     |
| pickup | 2300.0  | 9.4993   | 5.1532    | 242.12 | 446.32  | 1.84x  | False     |

density_plausible True: 0/60.

**Verdict: direction confirmed, mechanism FALSIFIED. Scored as a failed prediction.**

The rise was predicted, so a naive reading calls this a hit. It is not. The predicted
mechanism (silhouette sharpening) implies a small rise toward a converged value. The
observed 1.84-1.87x collapse in solid_volume is not convergence, and the real mechanism
invalidates the sweep. Recording this as a confirmation would bank the right answer for
the wrong reason and hide the bug.

Two pieces of evidence rule the predicted mechanism out:

1. **Particle scaling is 4.31x, not 8x.** Halving h must multiply particle count by 8
   for a solid body (volume scaling). Backed out of solid_volume = n_particles * h**3:
   n_grid=64 -> 9,216 particles at h=0.08009; n_grid=128 -> 39,738 at h=0.04005.
   Ratio 4.31x is area scaling, the signature of columns collapsing to a single cell.
2. **All three classes move by the same factor** (1.86, 1.87, 1.84) despite completely
   different geometry. A shape-dependent silhouette effect cannot produce a
   shape-independent constant. A discretization artifact can.

## Actual root cause: the vehicle hollows out at n_grid=128

`truck_trimmed.ply` is a SURFACE splat: 191,107 points, no interior.

`solidify_columns` bins points by `floor(pos / h)` and fills every occupied (x,y) column
from its lowest to its highest occupied cell.

- At h=0.080m (n_grid=64) a column is wide enough to catch both a roof point and an
  underbody point. zlo -> zhi spans the body, the column fills, the body is solid.
- At h=0.040m (n_grid=128) columns are 4x more numerous and many catch only ONE surface
  point. zlo == zhi, so the column fills exactly one cell. The body degenerates from a
  solid into a shell.

The binding constraint is the splat's native point spacing, not the grid. n_grid=128
refines straight past it. `fit_to_bbox` sets `vehicle.spacing = inf`, which forces
FloodScene to re-solidify at its own h every time, so there is no guard against this.

## Why this biases the sweep toward FORD

Buoyancy is rho_water * g * V_displaced. Body mass is still forced correct at 1390 kg,
but the body now displaces roughly half the water it should, so it is systematically
under-buoyant. The shell is also porous, so it blocks flow less and accumulates less
lateral drag. Both errors push the same direction: toward FORD.

v3 was widened specifically to find FORD conditions. The bug manufactures FORD. Taken at
face value these 60 rows would have "discovered" an artifact. This is the main reason the
manifest must not be read as results.

## The real tension (this is the finding worth keeping)

No single n_grid satisfies both constraints, because they are set by different things:

- **n_grid=64**: vehicle solidifies correctly, but water is under-resolved at shallow
  depth (pickup at 0.15m seeds 1 particle layer; 0.05m seeds 0 for pickup).
- **n_grid=128**: water is well resolved at every depth in the grid, but the vehicle
  hollows out.

Water resolution is governed by dx. Vehicle solidification is governed by the splat's
point spacing. Raising n_grid helps the first and breaks the second. The fix must
decouple the body's solidify pitch from the grid pitch, or densify the point cloud
before solidifying. Neither is a config change.

Note the domain formula is unchanged and correct here: lim = max(2.2*length, 3.5*width,
6.0*depth). The 6.0*depth term never binds below depth ~1.71m, so the domain is locked by
vehicle length and dx does not shrink as water gets shallower. That is why shallow depths
are hard in the first place.

## Historically-invalid pickup rows at depth=0.15m

v2 ran pickup at 0.15m with n_grid=64, seeding only 1 water particle layer.

At n_grid=128 preflight gives pickup depth=0.15m -> 3 water z-layers, clearing
MIN_Z_LAYERS=2. All 4 v3 rows at that cell (idx-0044 through idx-0047, one per velocity)
ran and plateaued.

Caveat that matters: the water at that cell is now adequately resolved, but the vehicle
in those same runs is hollow. The rows are not a valid replacement for v2's bad rows.
The water-resolution defect is fixed; a vehicle-geometry defect replaced it.

## Status of the 0.05m depth request

Dropped, not deferred. At n_grid=64 a 0.05m slab seeds 1 layer for sedan/suv and ZERO
for pickup (a run with no water at all, which would complete and report FORD). At
n_grid=128 it is still 1 layer. Reaching 2 layers needs n_grid=256, which is 64x v2's
cells and would hollow the vehicle far worse. 0.10m is the shallow floor for this solver.

## Next step (not done, needs a decision)

Fix vehicle solidification before any further n_grid=128 sweep. Options, in rough order
of effort:

1. Decouple body pitch from grid pitch: solidify at a fixed h tied to the splat's point
   spacing, independent of n_grid. Cheapest, but MPM wants body particle pitch near dx/2
   for the body to block flow, so this trades one error for another.
2. Densify the surface point cloud (resample/upsample) before solidify, so columns stay
   populated at finer h.
3. Watertight-mesh path with true interior fill instead of column fill.

A cheap diagnostic first: compute solid_volume across n_grid in {32, 48, 64, 96, 128}
and find where the 8x scaling law breaks. That locates the splat's effective point
spacing and tells us the maximum usable n_grid for this mesh. Pure numpy, no GPU.

## Artifact status

`data/track1_sweep_v3/manifest.csv` is a valid record of an INVALID experiment. Keep it
as a diagnostic artifact. Do not cite it as results, do not feed it to
`analysis/viability_audit.py`, do not put it on the poster.
