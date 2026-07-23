# v3 invalidation status: resolved (this file is current)

Date: 2026-07-22. Written to close the dispute created by two byte-identical copies of
the v3 invalidation writeup, one renamed "COMPLETELY WRONG ON 3 COUNTS dont use ...".
This file supersedes both of those and is the current record. Neither old file was
deleted; both are kept for provenance.

## The dispute

Two files existed in docs/:

- `track1_v3_sweep_invalid_hollow_vehicle.md` (the invalidation writeup)
- `COMPLETELY WRONG ON 3 COUNTS dont use track1_v3_sweep_invalid_hollow_vehicle.md`

Confirmed on 2026-07-22 that these are byte-identical: both hash to
`64e77565c158db2a0524486eb44c1d0c5d3c613a`, both 7378 bytes. The "COMPLETELY WRONG"
label is a filename only. No corrected content, no counter-argument, and no statement of
the three "counts" was ever written into either file. On the evidence in the repo, the
rename asserts an error without recording one.

## Verdict

The original hollow-vehicle invalidation reasoning HOLDS. The "COMPLETELY WRONG" rename
was the mistake, or at minimum is unsupported: it carries no evidence and is contradicted
by a fresh recomputation done for this file. The v3 sweep (n_grid=128) remains invalid and
must not be cited, plotted, or fed to analysis/viability_audit.py. Use v2 (n_grid=64),
filtered to density-plausible, sedan and pickup only, as already recorded in CLAUDE.md.

## Evidence (mesh and grid, not the rename)

1. The vehicle source is a surface-only splat. `data/truck_trimmed.ply` header, read
   directly: `element vertex 191107`, properties x/y/z plus normals and Gaussian
   spherical-harmonic coefficients (f_dc_*, f_rest_*), and no `element face`. It is a
   point cloud of the exterior with no interior fill.

2. `solidify_columns` (scripts/solidify_scaling_diagnostic.py, and the reference copy in
   citations/vehicle(kks32).py) bins points by `floor(pos / h)` and fills each occupied
   (x,y) column from its lowest to its highest occupied z cell. With a surface-only cloud,
   whether a column spans the body or collapses to a single cell depends entirely on
   whether that column happens to catch two surface points (roof and underbody) or one.
   That is set by the splat's native point spacing, not by the grid.

3. Fresh scaling diagnostic, run 2026-07-22 against the local mesh
   (base miniforge python, numpy 2.5.0, plyfile), n_grid in {32,48,64,96,128}. For a
   solid body the particle count scales as n_grid^3, so the fitted exponent p_exp should
   be near 3.0 and solid_volume should converge to a constant. Observed instead:

   | class  | dens@64 | dens@128 | vol@64 | vol@128 | p_exp range |
   |--------|---------|----------|--------|---------|-------------|
   | sedan  | 293.55  | 544.63   | 4.7352 | 2.5522  | 2.06 to 2.35 |
   | suv    | 308.13  | 575.62   | 6.4583 | 3.4571  | 2.06 to 2.35 |
   | pickup | 242.12  | 446.32   | 9.4993 | 5.1532  | 2.10 to 2.25 |

   p_exp sits near 2, not 3: area scaling, the signature of a shell. solid_volume shrinks
   monotonically as the grid refines (it does not converge), and density climbs far past
   the 100 to 300 kg/m3 plausibility band at n_grid=128. The 64-to-128 particle ratio is
   4.31x (9216 to 39738 for the sedan), not the 8x a solid requires. All three classes
   move by nearly the same factor despite different geometry, which a shape-dependent
   silhouette effect cannot produce but a discretization artifact can. Every number in the
   original writeup reproduced exactly.

## Honest nuance (does not change the verdict)

The shell mechanism is present at all resolutions, not only at n_grid=128. Even at
n_grid=64 the fitted exponent is about 2.2, so the body is not a true solid there either;
n_grid=64 is usable only because its derived density happens to land inside the
plausibility band (sedan 293.55, pickup 242.12; the SUV at 308.13 already fails and is
excluded). So "v2 usable, v3 invalid" is a density-plausibility call at a resolution where
the artifact stays in-band, not a claim that the v2 vehicle is watertight. The real fix,
still open, is to decouple the body's solidify pitch from the grid pitch or densify the
point cloud before solidifying, as the original writeup lays out.

## Pointers

- Current record: this file (docs/v3_invalidation_status.md).
- Superseded, kept for provenance: docs/track1_v3_sweep_invalid_hollow_vehicle.md and its
  "COMPLETELY WRONG ON 3 COUNTS" twin (byte-identical, no unique content).
- v3 sweep data was already archived in commit b141c48 (2026-07-18); do not re-archive.
- Diagnostic used: scripts/solidify_scaling_diagnostic.py (edit VEHICLE_PLY to the local
  data/truck_trimmed.ply to reproduce off-cluster).
