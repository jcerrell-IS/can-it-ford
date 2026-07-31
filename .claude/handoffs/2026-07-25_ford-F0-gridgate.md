# F0 grid gate: does the hollow-vehicle dead end transfer to the watertight Yaris?

Read-only plus one pure-numpy computation. No GPU, no idev, no solver, no edits, no commits.
Run on `login1.vista.tacc.utexas.edu`, cwd `/work/11603/jcerrell0629/vista/can-it-ford`.
Interpreter `/work/11603/jcerrell0629/vista/.venv/bin/python`, numpy 2.5.1, trimesh 4.12.2.

## THE VERDICT

**a. No. The hollowing failure does not transfer to the watertight Yaris. The opposite failure appears instead.** The ratio column never once falls below 1.0. It runs 3.039 down to 1.848 across n_grid 32 to 192, always ABOVE the hull volume, and it decreases monotonically as resolution rises. Hollowing would show as a ratio collapsing below 1.0 as columns went unoccupied. Nothing like that happens. The `truck_trimmed.ply` dead end was a property of a sparse surface-only splat, not of the algorithm, and it does not reproduce on a watertight mesh.

**b. None exists, at any tested n_grid.** No row satisfies both gates. Implied density passes everywhere, 102.18 to 168.04 kg/m3, all inside 100 to 300. The ratio gate fails everywhere: the best row is n_grid=192 at 1.848, still far outside 0.85 to 1.20. Extrapolating the trend, ratio would need roughly another factor-of-two refinement past 192 before approaching 1.20, and the trend is flattening, so that is not a safe extrapolation.

**c. Raising n_grid is no longer forbidden by the hollowing mechanism, and it is not sufficient either.** The specific blocker recorded in `AUDIT_RECONCILIATION_july17.md` does not apply to this mesh. Raising n_grid strictly improves the volume error, monotonically, with no reversal. So the fix for the 3-layer water resolution is permitted on those grounds. But it does not repair the volume error: even at 192 the body is 85 percent over-filled. Raising n_grid buys water resolution, not a correct vehicle volume.

## THE OVER-FILL IS THE REAL FINDING, and it is the bug you asked me to watch for

Every ratio is above 1.0, which is the case you flagged: **the underbody is bridged shut and buoyancy is overstated.** At n_grid=64, the operating point in current use, the solidified body occupies 8.5475 m3 against a true hull of 3.5427 m3, a **2.41x over-fill, 141 percent too much displaced volume**.

Buoyant force scales with displaced volume, so at n_grid=64 buoyancy is overstated by the same 2.41x for any fully submerged condition. That pushes every FLOAT verdict toward flotation and pushes normal force, and therefore traction, down. It is the opposite sign of error from hollowing and it is not corrected by refinement within the tested range.

Implied density is misleading here and should not be read as reassurance. It sits inside the 100 to 300 band at every resolution only because the band is wide and the over-fill drives density down rather than up. A density of 128.69 kg/m3 at n_grid=64 looks plausible and is produced by a body 2.41x too large.

## Item 3, the table

Mesh confirmed watertight by trimesh: `is_watertight True`, 655,308 faces, 327,212 vertices, `mesh.volume` = **3.542739 m3**, which independently confirms the 3.5427 hull figure rather than assuming it.

Extent as loaded, before any solidify: `(4.2826, 1.7461, 1.5175)` m, long axis along x.
`lim = max(2.2*ext[1], 3.5*ext[0], 6.0*0.30) = 14.9890`, giving `dx = 0.2342` at n_grid=64, which reproduces the known dx and confirms the axis convention. The swapped-axis reading gives 9.4216 and dx 0.1472, which does not match, so it is not the convention in use.

Sampling seeded with `np.random.seed(0)` before a single `mesh.sample(60_000)`, sampled once and reused across all six resolutions, mirroring the real code path where `load_vehicle` samples once and `solidify(h)` is then called per scene.

| n_grid | dx | h | n_particles | solid_volume | ratio vs 3.5427 | implied density | water layers |
|---|---|---|---|---|---|---|---|
| 32 | 0.4684 | 0.2342 | 838 | 10.7651 | 3.039 | 102.18 | 1 |
| 48 | 0.3123 | 0.1561 | 2,416 | 9.1960 | 2.596 | 119.62 | 2 |
| 64 | 0.2342 | 0.1171 | 5,323 | 8.5475 | 2.413 | 128.69 | 3 |
| 96 | 0.1561 | 0.0781 | 16,303 | 7.7567 | 2.189 | 141.81 | 4 |
| 128 | 0.1171 | 0.0586 | 36,740 | 7.3745 | 2.082 | 149.16 | 5 |
| 192 | 0.0781 | 0.0390 | 110,067 | 6.5460 | 1.848 | 168.04 | 8 |

Particle count scaling, 64 to 128: 36,740 / 5,323 = **6.90x**. A solid fill under a 2x refinement requires 8x. The July 17 postmortem measured 4.31x on `truck_trimmed.ply`. So the watertight Yaris scales much closer to solid than the splat did, 6.90 against 8, but still short, which is consistent with column bridging capturing a shrinking but nonzero excess as cells get finer.

## Item 4, water layers. Your expectation is confirmed.

`len(np.arange(3*dx + 0.5*h, 3*dx + 0.30, h))` at n_grid=64 returns **3**. Confirmed, not corrected.

The full column is in the table. Layer count rises 1, 2, 3, 4, 5, 8 across the six resolutions.

## Item 1, the sample call. Unseeded, and it takes neither a seed nor an rng.

`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py:162`, verbatim:

    pos = np.asarray(mesh.sample(60_000), dtype=np.float64)

`mesh.sample` is called with a count only. trimesh's signature accepts no seed or rng here as invoked, and no seeding is applied around the call.

**Precise distinction, because the file does contain seeding elsewhere and it would be easy to misread.** `FloodScene.__init__` at `:260` accepts `seed: int = 0` and builds `rng = np.random.default_rng(seed)` at `:270`, but that rng is consumed at `:298` for the **water jitter**, not for mesh sampling. The water is seeded. The vehicle surface sample is not. They are separate paths.

The file is **currently dirty on Vista**: `git diff --stat` shows 6 insertions, 2 deletions. Inspected, and the diff is confined to `FloodHistory.to_csv`, adding `vx,vy,vz,vmag,wx,wy,wz` columns. It does **not** touch line 162. So the quote above is the original code, not another session's in-flight edit. Not stashed, not reverted, not touched.

## Item 2, solidify. It bridges columns. It does not test interiority.

`solidify_columns(pos, h)` in the same file. The algorithm, read in full:

1. `key = np.floor(pos / h)` voxelizes the surface points at pitch h.
2. `np.lexsort` then `np.flatnonzero` groups the voxels into (x, y) columns.
3. For each column: `zlo, zhi = k[s, 2], k[e-1, 2]`, then `zs = np.arange(zlo, zhi + 1)`.
4. Every cell between the lowest and highest occupied z in that column is emitted.

So it **fills each (x, y) column floor-to-ceiling between its own extremes.** There is no inside/outside test, no ray cast, no winding number, no flood fill. Its own docstring states the tradeoff plainly: filling happens "at the cost of merging wheel wells and window openings into the solid; for blocking flow that is the right approximation."

**This is the mechanism that decides the whole question, and it explains both failure modes at once.** Because the algorithm never asks whether a point is inside the body, watertightness confers no benefit on interiority. What watertightness changes is column *occupancy*. A sparse splat leaves many columns empty, so the body hollows. A dense watertight mesh occupies nearly every column, so nothing hollows, and instead every concavity between the lowest and highest surface hit gets bridged: wheel wells, window openings, and the gap under the floor pan. That bridging is precisely the over-fill the ratio column measures.

The over-fill is therefore **by design, not a defect**, and it will not converge to 1.0 at any resolution. Refinement shrinks the bridged volume because cells get smaller, which is the monotone trend in the table, but the underbody stays closed as long as the algorithm bridges rather than tests interiority.

## Named, not guessed

1. **Whether ratio ever enters 0.85 to 1.20 above n_grid=192.** Not tested. The trend is decreasing and flattening; 192 to 1.20 would need a large further refinement and the extrapolation is not safe. n_grid=256 and 384 would settle it and cost only CPU.
2. **Whether the over-fill is acceptable for the intended physics.** The docstring calls bridging "the right approximation" for blocking flow. For blocking flow that is defensible. For a buoyancy or FLOAT verdict it is not obviously defensible at 2.41x. That is a modeling decision, not a measurement, and it is not mine to make.
3. **What the correct fix is.** Not proposed here. Options exist, a true interiority test or an explicit underbody mask, but choosing one changes the physics and belongs to whoever owns the solver.
4. **Whether the 60k sample count is itself limiting at fine h.** At n_grid=192, h=0.0390, 60,000 surface points spread over 110,067 emitted cells. Column occupancy may be sampling-limited there rather than geometry-limited. Not separated in this pass. Raising the sample count and re-running the same table would separate the two, and that is a pure-CPU test.
5. **`AUDIT_RECONCILIATION_july17.md` was not opened this pass.** Its findings are taken from the task brief. Absent from my read set on Mac and on Vista, not checked at either path.

---

# CORRECTION APPENDED 2026-07-25 by lane yaris-render (staleness gate S-1 / S-2)

This report's central verdict is **OBSOLETE**. It is retained verbatim above because its
mechanism analysis (section "Item 2, solidify") is correct and was the clue that led to the
fix. Its numeric conclusions are not.

**What was measured then:** `solidify_columns`, which bridges every (x,y) column between its
lowest and highest occupied cell. Section "Item 2" of this report diagnosed that mechanism
exactly right.

**What replaced it:** `solidify_watertight(mesh, h)`, exact vertical ray parity, live at
`/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py:88`. Still UNCOMMITTED.
`VehicleBody.solidify` dispatches to it when `mesh is not None and mesh.is_watertight`.

**Re-derived live 2026-07-25** on the Mac (miniforge can-it-ford env, trimesh 4.12.2,
numpy 2.5.1), executing the real functions AST-extracted from the live Vista `vehicle.py`:

| n_grid | h (m) | N | solid (m3) | ratio | rho at 1100 kg | water layers |
|---|---|---|---|---|---|---|
| 32 | 0.1472130 | 1188 | 3.79013 | 1.0698 | 290.23 | 2 |
| 48 | 0.0981420 | 3846 | 3.63558 | 1.0262 | 302.57 | 3 |
| 64 | 0.0736065 | 8904 | 3.55086 | 1.0023 | 309.78 | 4 |
| 96 | 0.0490710 | 29807 | 3.52203 | 0.9942 | 312.32 | 6 |
| 128 | 0.0368032 | 71160 | 3.54727 | 1.0013 | 310.10 | 8 |
| 192 | 0.0245355 | 240138 | 3.54687 | 1.0012 | 310.13 | 12 |

Three findings overturn this report's conclusions:

1. **"b. None exists, at any tested n_grid" is WRONG under the current code.** The ratio
   band 0.85-1.20 now passes at EVERY tested n_grid, and the tighter 0.95-1.10 band passes
   at every n_grid too. The over-fill was never a property of the mesh or the grid.
2. **"raising n_grid ... is not sufficient" no longer applies.** Raising n_grid is now
   permitted AND buys exactly what was wanted: water layers go 4 -> 6 -> 8 -> 12 at
   n_grid 64 -> 96 -> 128 -> 192, with volume error staying inside 0.6 percent. The
   4-layer depth-resolution limitation is now fixable by refinement.
3. **The density band is the thing that is wrong, not the vehicle.** This report warned
   "implied density is misleading here and should not be read as reassurance ... it sits
   inside the 100 to 300 band only because the over-fill drives density down." That warning
   is now confirmed quantitatively: at the correct volume, rho = 1100 / 3.5427 = 310.5
   kg/m3, which is ABOVE the project's 100-300 kg/m3 plausibility band. The band was being
   satisfied by a bug. Widen or restate the band; do not adjust the vehicle to re-enter it.

Also corrected: this report's item that `load_vehicle` cannot load the .ply. Verified live
2026-07-25: `is_watertight True`, volume 3.542739 m3, 655308 faces, 327212 vertices, oriented
extents [1.7461 4.2826 1.5175] m. It loads.

Also corrected: this report used `lim = 14.9890` from unswapped axes. `load_vehicle` rotates
the long horizontal axis onto y before `FloodScene` computes `lim`, so the operative value is
`lim = max(2.2*ext[1], 3.5*ext[0], 6.0*depth) = 9.42163 m` at depth 0.30, giving
dx 0.147213 and h 0.0736065. Confirmed against the live Vista run's own INSTRUMENT line.
