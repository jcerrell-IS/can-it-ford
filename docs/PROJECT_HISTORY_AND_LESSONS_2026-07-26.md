# Can It Ford: project history and lessons, compiled 2026-07-26

Built from git log (`~/can-it-ford`), `.claude/handoffs/` (31 files), `docs/GAP_MANIFEST_2026-07-25.md`,
and past claude.ai chat summaries. Every claim below has a commit hash, file path, or handoff
filename attached. If a number appears anywhere else without one of those, treat it as unverified
until it's checked against this file's sources directly.

---

## Part 1: the six phases, with commits

**Before Jul 1.** REU starts May 30. Tutorials done, abstract written and Kumar-approved June 18.
No repo yet.

**Jul 1-7, first result, then found fake.** `Can It Ford initial commit` (Jul 1). `Add 31-row phase
space results: 23 unique conditions, 16 L1/L2 divergence points` (Jul 2), this is the number that's
circulated ever since. Built on a hardcoded box and plane using Genesis SPH, not MPM, and not a real
reconstructed scene. Caught in an audit Jul 7, `add provisional status and corrections log, findings
under active revision`. Decision: rebuild for real MPM rather than rewrite the abstract.

**Jul 8-14, rebuild hits walls.** Vehicle mass and friction set for the first time (Jul 8, `add cited
vehicle_params.py`). Jul 9, honest status doc to Kumar naming two dead tracks. Jul 14, `Fix vehicle
rho regression: 604 to 115.7 for 1390kg sedan target`.

**Jul 15-20, mesh saga.** Two earlier reconstruction attempts had already failed (marching cubes
stalled at genus 9, Poisson gave a 0.345 m mismatched asset). Jul 17, real NCAC crash-test vehicle
files pulled in (Yaris, Silverado, both coarse and detailed). Jul 19, canonical hull confirmed. Jul
20, `push validated flood_vehicle render and metrics`.

**Jul 21-25, poster infrastructure, and the real turning point.** Methods section, citation audits,
provenance fields, mostly plumbing, UNTIL:

### The actual breakthrough: Jul 25, `solidify_watertight`

Source: `.claude/handoffs/2026-07-25_MPM-REAL-yaris-verified.md`, in full.

The vehicle-solidification function `solidify_columns` fills every (x,y) column from its lowest to
highest occupied cell. On a watertight car hull that bridges ground clearance and wheel wells solid,
by construction, at any resolution. Measured overfill 2.18x at n_grid=64, buoyancy overstated 1.64x.

Fix: `solidify_watertight(mesh, h)` in `src/warpmpm/vehicle.py`, exact vertical ray parity. Per grid
column, collect every z where the column crosses the surface, sort, fill only between entry/exit
pairs. Verified across four resolutions:

```
n_grid   N        ratio     rho
  48    3846     1.0262   302.56
  64    8904     1.0023   309.78
  96    29807    0.9942   312.31
 128    71154    1.0012   310.12
```

True hull volume 3.54274 m3, target rho 310.49, realized mass 1100.00 kg at every row. This is the
result behind "the car is too light" in every later draft. Job 866214 (gh-dev, c642-011): final
|d| = 0.09043 m, yaw +1.2506, roll +0.0094, pitch -0.0035, depth 0.30 m, surge 1.5 m/s, n_grid 64.
This is where the poster's 0.0924 m dry-start figure traces to (0.09043 on disk, 0.09240 reproduced
in a later session, +2.2%, within expected jitter, see Part 3).

**Status as of tonight: this patch is uncommitted.** It lives only as a working-tree edit on Vista
at `/work/11603/jcerrell0629/vista/mpm-engine/src/warpmpm/vehicle.py`, HEAD `fd390d6`. Also
uncommitted in the same file: the six-DOF CSV columns (vx,vy,vz,vmag,wx,wy,wz) added in a different
session. Both need to survive the same commit.

**Jul 26, today's sprint.** Realized the material-point vs rigid-body confusion, imposed mass
directly, ran velocity and mass sweeps, found and fixed the real AR&R implementation bug (23/70),
found grid non-convergence, self-corrected "can't see mass" to "coarse not blind."

---

## Part 2: three separate comparisons existed, not one

The project ran three distinct L1-vs-something checks this week. They answer different questions
and don't all point the same way.

1. **70-cell scenario grid, L1 only, no L2.** The "23 of 70" audit. Verified live, byte-identical,
   multiple sessions. This is an implementation-correctness claim, not a physics claim.
2. **Six-point velocity sweep, one mass, L1 vs L2.** "2 of 6 points diverge." Verified.
3. **Three-mass class sweep, L1 vs L2, same scenario.** Per `GAP_MANIFEST_2026-07-25.md` gap #3, at
   nominal 0.30 m / 1.5 m/s: small_passenger both NO-FORD (agree), large_4wd both FORD (agree), only
   large_passenger disagrees. **Two of three classes agree.** This is the opposite direction from 1
   and 2, and it currently doesn't appear anywhere in the Slack draft or, per the gap manifest, on
   the poster's own divergence-zone text as of Jul 25 evening.

If asked "does the rule agree with the sim," the honest answer depends on which of the three is
meant. Recommend naming all three explicitly wherever this gets written up formally.

## Part 3: the sharpest unresolved finding, currently undersold

Same source, gap #10. Nominal D x V at the vehicle is 0.4500 m2/s. The *locally measured* D x V,
using actual depth and speed at the car rather than requested inputs, is 0.1892 / 0.1645 / 0.1530,
58 to 66 percent lower. Using local instead of nominal flips large_passenger FORD to NO-FORD and
makes L1 and L2 agree on all three classes. Quoted verbatim from the source: "Which definition AR&R
intends is unresolved and it is the whole ballgame for that class."

This is a stronger, more citable finding than "the rule can't see mass, only the product can" and
it isn't in the current draft to Kumar. Consider raising it as its own question.

## Part 4: numbers confirmed dead, do not resurrect

| number | status | source |
|---|---|---|
| Fill ratio 0.954 at n_grid=128 | Retracted same session it appeared. Voxel-shell leakage at sparse sampling, correct value ~1.99 at 6M samples. | `2026-07-25_MPM-REAL-yaris-verified.md` |
| Drift 0.1198 m | Zero occurrences across all 126 session logs (115 MB) plus docs and handoffs. | `INDEX.md`, 2026-07-26 00:27 correction |
| "load_vehicle cannot load this .ply at all" | False, corrected same day. Loads fine, watertight, 3.5427 m3. | `INDEX.md`, `2026-07-25_ford-F0-gridgate.md` correction |
| F0's "no n_grid passes the ratio band" | True only for the old buggy solidify_columns. Re-derived: passes at every n_grid 32-192 under the fix. | `2026-07-25_ford-F0-gridgate.md`, corrected 00:27 |
| Vehicle rho as "91.6 kg/m3" | Corrected in the same session it appeared; script actually runs 115.7 kg target 1390 kg. | `2026-07-25_vista.md` |
| Rho 604 or 579.06 in `simulation/can_it_ford_L2.py` | Both stale at different times; that file is a different, disused script from the one everything above traces to (`renders/yaris_render_s1/sim_standing.py`). Don't conflate the two. | git log, `CLAIM_REGISTER.md` D-7 |

## Part 5: two honest asterisks

- **Particle count is not perfectly bit-reproducible run to run.** `mesh.sample(60_000)` in
  `vehicle.py` is unseeded, so oriented placement jitters slightly: 8904 particles locally, 8905 on
  Vista, from identical inputs, about 0.01 percent. The `determinism_identical: true` field checks
  two loads inside one script invocation, which is real, but doesn't cover invocation-to-invocation
  variance. If this gets pushed on, the honest answer is "reproducible within about 0.01 percent of
  particle count, not bit-identical across machines."
- **A `git filter-repo` rewrite once lost edits** to README, SESSION_STATE.md, and paper_draft.md,
  recovered from a pre-purge filesystem backup (commit `ca91b12`). Nothing permanently lost, but
  never run filter-repo again without a filesystem backup taken first.

## Part 6: infrastructure pain worth remembering

- Vista login node ffmpeg is broken (`libunwind.so.8` missing); compute nodes have no ffmpeg at all.
  Encode on the Mac from pulled frames, every time.
- `from warpmpm.vehicle import load_vehicle` blocks on the Vista login node, exceeded a 240s timeout
  twice. Completes in ~79s on a compute node. Budget for this, don't debug it as a code bug.
- Two `mpm-engine` trees coexist on disk (`/work/.../vista/mpm-engine` installed vs
  `can-it-ford/mpm-engine` stale nested copy). The stale one already caused one false blocker in an
  earlier session. Still there.
- `analysis/` figure scripts (`plot_l1_three_class.py`, `plot_traction_bias.py`,
  `plot_geometry_pipeline.py`, `recompute_l1_l2.py`) are untracked. A clean clone reproduces none of
  the current poster figures without them.

## Part 7: what to do, in order

1. **Commit `vehicle.py` on Vista tonight.** The `solidify_watertight` fix and the 6-DOF CSV columns
   are both uncommitted in the same file. This is the single highest-risk open item in the whole
   project right now, everything since Jul 25 depends on it existing.
2. **Decide the D x V definition question**, nominal or local, before the poster locks. It changes
   a verdict and the source doesn't settle it.
3. **State the 2-of-3-classes agreement** wherever disagreement is claimed, so poster and paper don't
   contradict the project's own gap manifest.
4. **Commit the untracked analysis scripts** so a clean clone can reproduce the poster figures.
5. **Restate or widen the 100-300 kg/m3 density band**, not the vehicle. Correct density is 310.5,
   above the band, only because the old buggy function's overfill used to dilute it into range.
6. **Never cite** the dead numbers in Part 4, or `simulation/can_it_ford_L2.py`'s rho value, without
   checking which script actually produced the number in question first.
