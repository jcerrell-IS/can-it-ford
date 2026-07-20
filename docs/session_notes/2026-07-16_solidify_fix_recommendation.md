# Solidify hollow-vehicle bug: diagnostic + fix recommendation

Date: 2026-07-16. Scope: diagnostic pass only. No fix implemented. Waiting for
confirmation before touching `ford_sweep_driver.py` or the solidify logic.

## 0. Skill-presence check (requested first)

`~/.claude/skills/` currently contains exactly:

- `bug-triage-protocol/`   (EMPTY: directory exists, no `SKILL.md` inside)
- `can-it-ford-cluster/`   (SKILL.md, 4544 bytes)
- `can-it-ford-output/`    (SKILL.md, 7823 bytes)
- `can-it-ford-science/`   (SKILL.md, 6230 bytes)

`mpm-technical-deep-reference` and `mpm-render-pipeline` are NOT installed. They do
not exist on Vista. This pass was done without them. `bug-triage-protocol` is also
effectively absent (empty folder, no skill file).

## 1. Doc claims verified against live code (not assumed)

`solidify_columns` does NOT live in `simulation/can_it_ford_L2_mpm.py` (that file only
has `to_np`, `debatch`, `sample_fields`, `main`). It lives in
`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py:59`. Read directly:

- It bins points by `floor(pos/h)`, then fills every occupied (x,y) column from its
  lowest to highest occupied cell. Doc's description is accurate.
- `fit_to_bbox` (driver:56 and vehicle.py) sets `vehicle.spacing = float("inf")`
  (driver:69). Confirmed.
- `FloodScene.__init__` re-solidifies at `h = dx/2`, `dx = lim/n_grid`, guarded by
  `if vehicle.spacing > 1.2*h` (vehicle.py:240,245-246). Since spacing=inf it always
  re-solidifies at the grid's own pitch. Confirmed.
- Mass is forced correct: `vehicle_density = vehicle_mass / solid_volume`,
  `solid_volume = n_particles * h**3` (vehicle.py:248-251). Confirmed.
- `load_gaussians_ply` reads all 191,107 vertices with NO opacity filter or masking,
  so the solidify input is the full raw point cloud. Confirmed.
- lim formula `max(2.2*length, 3.5*width, 6.0*depth)`: the 6.0*depth term never binds
  for any sweep cell (max 3.6 at depth 0.60 vs geometry terms 10.25/10.91/12.96), so
  lim (and therefore h) is depth-independent. Confirmed.

## 2. Diagnostic built and run (pure numpy, no GPU, ran on login2)

`scripts/solidify_scaling_diagnostic.py`. Replicates the exact geometry path
(orient, long-axis-along-y, center, `fit_to_bbox` anisotropic scale to each class
bbox) and copies `solidify_columns` verbatim. For n_grid in {32,48,64,96,128} it
computes h=dx/2, particle count, solid_volume = n*h^3, density = mass/vol.

`p_exp` is the scaling exponent between consecutive grids: n_particles proportional
to n_grid^p. p=3 means true volume (solid) scaling, p=2 means area (shell) scaling.

### Faithfulness cross-check (this validates the script)

All twelve v3-manifest numbers reproduce EXACTLY from geometry alone:

| class  | vol64 (mine=manifest) | dens64 | vol128 (mine=manifest) | dens128 |
|--------|-----------------------|--------|------------------------|---------|
| sedan  | 4.7352                | 293.55 | 2.5522                 | 544.63  |
| suv    | 6.4583                | 308.13 | 3.4571                 | 575.62  |
| pickup | 9.4993                | 242.12 | 5.1532                 | 446.32  |

Sedan particle counts 9216 (n64) and 39738 (n128) match the doc's back-out; ratio
4.31x confirmed. Solidify is fully deterministic (no rng), which is why it reproduces
to 4 decimals.

### Scaling result (sedan; suv/pickup identical shape)

| n_grid | h_m     | n_part | solid_vol | density | p_exp |
|--------|---------|--------|-----------|---------|-------|
| 32     | 0.16019 | 1864   | 7.6618    | 181.42  |  -    |
| 48     | 0.10679 | 4827   | 5.8788    | 236.44  | 2.347 |
| 64     | 0.08009 | 9216   | 4.7352    | 293.55  | 2.248 |
| 96     | 0.05340 | 21230  | 3.2320    | 430.07  | 2.058 |
| 128    | 0.04005 | 39738  | 2.5522    | 544.63  | 2.179 |

**p never reaches 3 anywhere in the tested range.** It sits at 2.1-2.35 throughout.
solid_volume drops by ~0.54x per doubling (a true solid would hold roughly constant,
ratio ~1.0; a pure shell gives 0.5). So the body is shell-dominated at EVERY tested
resolution, including n_grid=32.

## 3. Second, independent verification (the doc's framing was too clean)

The exponent result contradicts the doc's "n64 solidifies correctly, n128 hollows
out" (which implies a transition between 64 and 128). Before reporting, I verified the
mechanism a different way: `scripts/solidify_column_height_probe.py` measures, per
grid, the fraction of single-cell columns and the mean column fill height vs the body
height in cells.

### Sedan

| n_grid | h_m     | n_cols | body_tall | frac_1cell | mean_h | mean_h/body_tall |
|--------|---------|--------|-----------|------------|--------|------------------|
| 32     | 0.16019 | 347    | 9.0       | 0.078      | 5.37   | 0.60             |
| 48     | 0.10679 | 735    | 13.5      | 0.118      | 6.57   | 0.49             |
| 64     | 0.08009 | 1234   | 18.0      | 0.139      | 7.47   | 0.41             |
| 96     | 0.05340 | 2346   | 27.0      | 0.187      | 9.05   | 0.33             |
| 128    | 0.04005 | 3818   | 36.0      | 0.223      | 10.41  | 0.29             |

suv and pickup track this within a couple percent.

Reading:

- The doc's mechanism (columns fragmenting into single cells as h shrinks) is real and
  directional: frac_1cell rises 0.078 -> 0.223. Confirmed a second way.
- BUT single-cell columns are a minority even at n128 (22%). The dominant effect is
  that columns fill a SHRINKING fraction of the body height: mean_h/body_tall falls
  0.60 -> 0.29. For a true solid this ratio is a shape property and should be roughly
  constant across h. Its steady decline IS the hollowing.
- The degradation is CONTINUOUS from n32 upward, not a switch between 64 and 128.
  n_grid=64 is not a valid solid, it is only less hollow than 128 (fill fraction
  already 0.41, i.e. columns bridge only ~40% of the body height).

### Two independent causes (decomposing n64 -> n128)

solid_vol = n_cols * mean_h * h^3.

- In-plane: n_cols grows 3.09x (ideal 4x for area scaling). Not enough surface points
  to occupy every fine (x,y) column.
- Vertical: mean_h grows 1.39x (ideal 2x). Columns increasingly catch only one surface
  (roof OR floor), not both, so they stop bridging the interior.

Both underperform, both are symptoms of the same root cause: `truck_trimmed.ply` is a
191k-point SURFACE with no interior, and column fill cannot manufacture a scale-stable
solid from it at any pitch.

## 4. Where the 8x law breaks

It does not hold anywhere in {32..128}. It is already broken at n_grid=32 (h~0.16m),
the coarsest resolution tested. The splat's effective spacing is coarser than the
grid pitch even there, so there is NO maximum usable n_grid that yields a real solid
body via column fill. This is a stronger, more pessimistic result than the doc's, and
it changes the recommendation.

## 5. Recommendation: Option 3 (watertight mesh + true interior fill)

Not the cheapest option, and here is why the cheaper two do not fix the measured
defect:

- **Option 1 (pin body pitch to a coarse fixed h, decouple from grid).** This would be
  correct IF a coarse h gave a solid body and the only problem were refining past it.
  The data says otherwise: even n_grid=32's h is already shell-like (fill fraction
  0.60 and falling, p<2.4). Pinning to a coarse h just freezes the LEAST-hollow shell.
  Worse, with the fluid grid at dx=0.04 (n128, which the water resolution needs) and
  body particles pinned at h~0.16, the body lattice is 4x coarser than the fluid cells,
  so fluid streams through the gaps. It trades vertical hollowness for horizontal
  porosity. Relocates the error, does not remove it.
- **Option 2 (densify/upsample the surface point cloud before solidify).** Fixes only
  the in-plane half (n_cols occupancy). Denser roof + denser floor points still leave
  each fine column catching only its local surface, so vertical bridging
  (mean_h/body_tall) is not fixed. Surface upsampling adds no interior, and the
  vertical cause is the slightly larger of the two. Insufficient as written.
- **Option 3 (watertight surface reconstruction, e.g. Poisson or alpha-shape, then
  voxel-fill the interior by point-in-mesh / flood fill).** This is the only path that
  gives n_particles proportional to true volume/h^3 (p=3) at all h. It produces a
  genuinely solid, non-porous body with correct displaced volume, so buoyancy and
  flow-blocking are both right at the n_grid the water resolution demands. It removes
  the artifact instead of relocating it.

Net: the breakdown is not "refine past a good h," it is "column fill can't build a
solid from a bare surface at any h." That is exactly the failure mode Option 3 exists
to fix.

## 6. Not done this pass (waiting for confirmation)

- No edits to `ford_sweep_driver.py` or `solidify_columns` / the solidify path.
- Two read-only diagnostics added under `scripts/`
  (`solidify_scaling_diagnostic.py`, `solidify_column_height_probe.py`).
- Awaiting go/no-go on implementing Option 3 (or a decision to accept n_grid=64 as a
  known-approximate body with an explicit buoyancy/porosity caveat, if the timeline
  rules out a watertight path).
